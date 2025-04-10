import json
import os
import sys
import pickle  # 不安全序列化，故意引入的安全問題
from datetime import datetime
from typing import Dict, List, Optional

class Book:
    """表示一本書的類別"""
    
    def __init__(self, title: str, author: str, isbn: str, published_year: int):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.published_year = published_year
        self.is_checked_out = False
        
    def check_out(self):
        """借出書籍"""
        if not self.is_checked_out:
            self.is_checked_out = True
            return True
        return False
    
    def check_in(self):
        """歸還書籍"""
        if self.is_checked_out:
            self.is_checked_out = False
            return True
        return False
    
    def to_dict(self):
        """將書籍轉換為字典"""
        return {
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'published_year': self.published_year,
            'is_checked_out': self.is_checked_out
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """從字典創建書籍"""
        book = cls(data['title'], data['author'], data['isbn'], data['published_year'])
        book.is_checked_out = data['is_checked_out']
        return book

class User:
    """表示系統用戶的類別"""
    
    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.checked_out_books: List[str] = []  # 存儲ISBN列表
        
    def check_out_book(self, isbn: str):
        """用戶借書"""
        if isbn not in self.checked_out_books:
            self.checked_out_books.append(isbn)
            return True
        return False
    
    def return_book(self, isbn: str):
        """用戶還書"""
        if isbn in self.checked_out_books:
            self.checked_out_books.remove(isbn)
            return True
        return False
    
    def to_dict(self):
        """將用戶轉換為字典"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'checked_out_books': self.checked_out_books
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """從字典創建用戶"""
        user = cls(data['user_id'], data['name'], data['email'])
        user.checked_out_books = data.get('checked_out_books', [])
        return user

class Library:
    """圖書館管理系統主類別"""
    
    def __init__(self):
        self.books: Dict[str, Book] = {}  # ISBN到Book的映射
        self.users: Dict[str, User] = {}  # user_id到User的映射
        self.load_data()  # 故意沒有錯誤處理
        
    def add_book(self, book: Book):
        """添加新書"""
        if book.isbn in self.books:
            print(f"錯誤：ISBN {book.isbn} 已存在")
            return False
        
        self.books[book.isbn] = book
        return True
    
    def remove_book(self, isbn: str):
        """移除書籍"""
        if isbn in self.books:
            del self.books[isbn]
            return True
        return False
    
    def add_user(self, user: User):
        """添加用戶"""
        if user.user_id in self.users:
            print(f"錯誤：用戶ID {user.user_id} 已存在")
            return False
        
        self.users[user.user_id] = user
        return True
    
    def remove_user(self, user_id: str):
        """移除用戶"""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
    
    def check_out_book(self, user_id: str, isbn: str):
        """借出書籍"""
        if user_id not in self.users:
            print(f"錯誤：用戶ID {user_id} 不存在")
            return False
        
        if isbn not in self.books:
            print(f"錯誤：ISBN {isbn} 不存在")
            return False
        
        user = self.users[user_id]
        book = self.books[isbn]
        
        if book.check_out():
            return user.check_out_book(isbn)
        return False
    
    def return_book(self, user_id: str, isbn: str):
        """歸還書籍"""
        if user_id not in self.users:
            print(f"錯誤：用戶ID {user_id} 不存在")
            return False
        
        if isbn not in self.books:
            print(f"錯誤：ISBN {isbn} 不存在")
            return False
        
        user = self.users[user_id]
        book = self.books[isbn]
        
        if book.check_in():
            return user.return_book(isbn)
        return False
    
    def find_books_by_author(self, author: str) -> List[Book]:
        """根據作者查找書籍"""
        return [book for book in self.books.values() if book.author == author]
    
    def find_books_by_title(self, title: str) -> List[Book]:
        """根據書名查找書籍"""
        return [book for book in self.books.values() if title.lower() in book.title.lower()]
    
    def get_overdue_books(self) -> List[Book]:
        """獲取逾期書籍 - 故意未實現的方法"""
        pass  # 未實現的方法，SonarQube 會檢測到
    
    def save_data(self):
        """保存數據到文件"""
        data = {
            'books': {isbn: book.to_dict() for isbn, book in self.books.items()},
            'users': {user_id: user.to_dict() for user_id, user in self.users.items()}
        }
        
        # 使用不安全序列化方法 (故意引入的安全問題)
        with open('library_data.pkl', 'wb') as f:
            pickle.dump(data, f)
        
        # 同時保存JSON版本 (安全方法)
        with open('library_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """從文件加載數據"""
        if os.path.exists('library_data.pkl'):
            with open('library_data.pkl', 'rb') as f:
                data = pickle.load(f)  # 不安全反序列化
            
            self.books = {isbn: Book.from_dict(book_data) for isbn, book_data in data.get('books', {}).items()}
            self.users = {user_id: User.from_dict(user_data) for user_id, user_data in data.get('users', {}).items()}
        elif os.path.exists('library_data.json'):
            with open('library_data.json', 'r') as f:
                data = json.load(f)
            
            self.books = {isbn: Book.from_dict(book_data) for isbn, book_data in data.get('books', {}).items()}
            self.users = {user_id: User.from_dict(user_data) for user_id, user_data in data.get('users', {}).items()}
    
    def generate_report(self):
        """生成報告"""
        report = {
            'total_books': len(self.books),
            'total_users': len(self.users),
            'checked_out_books': sum(1 for book in self.books.values() if book.is_checked_out),
            'oldest_book': None,
            'newest_book': None
        }
        
        if self.books:
            oldest = min(self.books.values(), key=lambda x: x.published_year)
            newest = max(self.books.values(), key=lambda x: x.published_year)
            report['oldest_book'] = oldest.title
            report['newest_book'] = newest.title
        
        return report

def display_menu():
    """顯示主菜單"""
    print("\n圖書管理系統")
    print("1. 添加書籍")
    print("2. 移除書籍")
    print("3. 添加用戶")
    print("4. 移除用戶")
    print("5. 借書")
    print("6. 還書")
    print("7. 查找書籍")
    print("8. 生成報告")
    print("9. 退出")

def get_input(prompt, required=True):
    """獲取用戶輸入"""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("錯誤：此項為必填")

def main():
    """主程式入口"""
    library = Library()
    
    while True:
        display_menu()
        choice = get_input("請選擇操作: ")
        
        try:
            if choice == '1':
                # 添加書籍
                title = get_input("書名: ")
                author = get_input("作者: ")
                isbn = get_input("ISBN: ")
                year = int(get_input("出版年份: "))
                
                book = Book(title, author, isbn, year)
                if library.add_book(book):
                    print("書籍添加成功")
                else:
                    print("添加書籍失敗")
            
            elif choice == '2':
                # 移除書籍
                isbn = get_input("ISBN: ")
                if library.remove_book(isbn):
                    print("書籍移除成功")
                else:
                    print("移除書籍失敗")
            
            elif choice == '3':
                # 添加用戶
                user_id = get_input("用戶ID: ")
                name = get_input("姓名: ")
                email = get_input("Email: ")
                
                user = User(user_id, name, email)
                if library.add_user(user):
                    print("用戶添加成功")
                else:
                    print("添加用戶失敗")
            
            elif choice == '4':
                # 移除用戶
                user_id = get_input("用戶ID: ")
                if library.remove_user(user_id):
                    print("用戶移除成功")
                else:
                    print("移除用戶失敗")
            
            elif choice == '5':
                # 借書
                user_id = get_input("用戶ID: ")
                isbn = get_input("ISBN: ")
                if library.check_out_book(user_id, isbn):
                    print("借書成功")
                else:
                    print("借書失敗")
            
            elif choice == '6':
                # 還書
                user_id = get_input("用戶ID: ")
                isbn = get_input("ISBN: ")
                if library.return_book(user_id, isbn):
                    print("還書成功")
                else:
                    print("還書失敗")
            
            elif choice == '7':
                # 查找書籍
                print("\n查找選項:")
                print("1. 按作者查找")
                print("2. 按書名查找")
                search_choice = get_input("請選擇查找方式: ")
                
                if search_choice == '1':
                    author = get_input("作者姓名: ")
                    books = library.find_books_by_author(author)
                elif search_choice == '2':
                    title = get_input("書名: ")
                    books = library.find_books_by_title(title)
                else:
                    print("無效選擇")
                    continue
                
                if books:
                    print("\n找到的書籍:")
                    for book in books:
                        status = "已借出" if book.is_checked_out else "可借"
                        print(f"{book.title} - {book.author} ({book.published_year}) [{status}]")
                else:
                    print("未找到匹配的書籍")
            
            elif choice == '8':
                # 生成報告
                report = library.generate_report()
                print("\n圖書館報告:")
                print(f"總書籍數: {report['total_books']}")
                print(f"總用戶數: {report['total_users']}")
                print(f"已借出書籍數: {report['checked_out_books']}")
                if report['oldest_book']:
                    print(f"最舊的書: {report['oldest_book']}")
                    print(f"最新的書: {report['newest_book']}")
            
            elif choice == '9':
                # 退出
                library.save_data()
                print("感謝使用圖書管理系統")
                break
            
            else:
                print("無效選擇，請重試")
        
        except ValueError as e:
            print(f"輸入錯誤: {e}")
        except Exception as e:
            print(f"發生錯誤: {e}")  # 過於寬泛的異常捕獲，SonarQube會檢測到

if __name__ == "__main__":
    main()
